from __future__ import annotations

import base64
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin

from playwright.sync_api import Locator, Page, TimeoutError as PlaywrightTimeoutError

_FIND_TEXT_MATCHES_SCRIPT = r"""(terms) => {
    const normalize = value => value.trim().replace(/\s+/g, " ");
    const visible = element =>
        element.getClientRects().length > 0
        && getComputedStyle(element).visibility !== "hidden"
        && getComputedStyle(element).display !== "none";
    const selectorFor = element => {
        const parts = [];
        while (element && element.nodeType === Node.ELEMENT_NODE) {
            let part = element.tagName.toLowerCase();
            if (element.id) {
                part += `#${CSS.escape(element.id)}`;
                parts.unshift(part);
                break;
            }
            const siblings = Array.from(element.parentElement?.children ?? [])
                .filter(sibling => sibling.tagName === element.tagName);
            if (siblings.length > 1) {
                part += `:nth-of-type(${siblings.indexOf(element) + 1})`;
            }
            parts.unshift(part);
            element = element.parentElement;
        }
        return parts.join(" > ");
    };

    const elements = Array.from(document.body.querySelectorAll("*")).filter(visible);
    const results = [];
    for (const term of terms) {
        const candidates = elements.filter(element =>
            normalize(element.innerText || "").toLocaleLowerCase()
                .includes(term.toLocaleLowerCase())
        );
        for (const element of candidates) {
            const hasMatchingChild = Array.from(element.children).some(child =>
                visible(child)
                && normalize(child.innerText || "").toLocaleLowerCase()
                    .includes(term.toLocaleLowerCase())
            );
            if (!hasMatchingChild) {
                const text = normalize(element.innerText || "");
                results.push({
                    term,
                    text,
                    selector: selectorFor(element),
                    className: element.getAttribute("class") || "(no class)",
                });
            }
        }
    }
    return results;
}"""

_COMPARE_IMAGES_SCRIPT = r"""async ({actual, baseline, minimumSimilarity}) => {
    const loadImage = source => new Promise((resolve, reject) => {
        const image = new Image();
        image.onload = () => resolve(image);
        image.onerror = () => reject(new Error("Could not decode image"));
        image.src = source;
    });

    const [actualImage, baselineImage] = await Promise.all([
        loadImage(actual),
        loadImage(baseline),
    ]);
    const canvas = document.createElement("canvas");
    canvas.width = baselineImage.naturalWidth;
    canvas.height = baselineImage.naturalHeight;
    const context = canvas.getContext("2d", { willReadFrequently: true });
    if (!context) {
        throw new Error("Could not create image comparison canvas");
    }
    context.drawImage(actualImage, 0, 0, canvas.width, canvas.height);
    const actualPixels = context.getImageData(0, 0, canvas.width, canvas.height).data;
    context.clearRect(0, 0, canvas.width, canvas.height);
    context.drawImage(baselineImage, 0, 0, canvas.width, canvas.height);
    const baselinePixels = context.getImageData(0, 0, canvas.width, canvas.height).data;
    let matchingPixels = 0;
    const pixelCount = actualPixels.length / 4;
    for (let index = 0; index < actualPixels.length; index += 4) {
        if (
            actualPixels[index] === baselinePixels[index]
            && actualPixels[index + 1] === baselinePixels[index + 1]
            && actualPixels[index + 2] === baselinePixels[index + 2]
            && actualPixels[index + 3] === baselinePixels[index + 3]
        ) {
            matchingPixels += 1;
        }
    }
    const similarity = matchingPixels / pixelCount * 100;
    return {
        matches: similarity >= minimumSimilarity,
        reason: `${similarity.toFixed(2)}% matching pixels (minimum ${minimumSimilarity}%)`,
    };
}"""

_COMPARE_SVGS_SCRIPT = r"""async ({actual, baseline, styles, minimumSimilarity}) => {
    const parseSvg = (markup, expectedName = null) => {
        const parser = new DOMParser();
        let parsed = parser.parseFromString(markup, "image/svg+xml");
        if (parsed.querySelector("parsererror")) {
            parsed = parser.parseFromString(
                `<svg xmlns="http://www.w3.org/2000/svg">${markup}</svg>`,
                "image/svg+xml"
            );
            if (parsed.querySelector("parsererror")) {
                throw new Error("Could not parse SVG image");
            }
            const candidates = Array.from(
                parsed.documentElement.querySelectorAll(":scope > svg")
            );
            const matching = candidates.find(
                candidate => candidate.getAttribute("data-name") === expectedName
            );
            if (!matching) {
                throw new Error(
                    `Could not find SVG baseline${expectedName ? ` for ${expectedName}` : ""}`
                );
            }
            return matching;
        }
        return parsed.documentElement;
    };
    const renderableSvg = (markup, expectedName = null) => {
        const svg = parseSvg(markup, expectedName);
        for (const use of Array.from(svg.querySelectorAll("use"))) {
            const href = use.getAttribute("href")
                || use.getAttributeNS("http://www.w3.org/1999/xlink", "href");
            if (!href || !href.startsWith("#")) continue;
            const symbol = document.getElementById(href.slice(1));
            if (!symbol) continue;
            let defs = svg.querySelector("defs");
            if (!defs) {
                defs = document.createElementNS("http://www.w3.org/2000/svg", "defs");
                svg.insertBefore(defs, svg.firstChild);
            }
            defs.appendChild(symbol.cloneNode(true));
        }
        Object.assign(svg.style, styles);
        return "data:image/svg+xml;charset=utf-8," + encodeURIComponent(
            new XMLSerializer().serializeToString(svg)
        );
    };
    const actualSvg = parseSvg(actual);
    const expectedName = actualSvg.getAttribute("data-name");
    const loadImage = source => new Promise((resolve, reject) => {
        const image = new Image();
        image.onload = () => resolve(image);
        image.onerror = () => reject(new Error("Could not render SVG image"));
        image.src = source;
    });

    const [actualImage, baselineImage] = await Promise.all([
        loadImage(renderableSvg(actual)),
        loadImage(renderableSvg(baseline, expectedName)),
    ]);
    const canvas = document.createElement("canvas");
    canvas.width = baselineImage.naturalWidth;
    canvas.height = baselineImage.naturalHeight;
    const context = canvas.getContext("2d", { willReadFrequently: true });
    if (!context) throw new Error("Could not create image comparison canvas");
    context.drawImage(actualImage, 0, 0, canvas.width, canvas.height);
    const actualPixels = context.getImageData(0, 0, canvas.width, canvas.height).data;
    context.clearRect(0, 0, canvas.width, canvas.height);
    context.drawImage(baselineImage, 0, 0, canvas.width, canvas.height);
    const baselinePixels = context.getImageData(0, 0, canvas.width, canvas.height).data;
    let matchingPixels = 0;
    const pixelCount = actualPixels.length / 4;
    for (let index = 0; index < actualPixels.length; index += 4) {
        if (
            actualPixels[index] === baselinePixels[index]
            && actualPixels[index + 1] === baselinePixels[index + 1]
            && actualPixels[index + 2] === baselinePixels[index + 2]
            && actualPixels[index + 3] === baselinePixels[index + 3]
        ) {
            matchingPixels += 1;
        }
    }
    const similarity = matchingPixels / pixelCount * 100;
    return {
        matches: similarity >= minimumSimilarity,
        reason: `${similarity.toFixed(2)}% matching pixels (minimum ${minimumSimilarity}%)`,
    };
}"""


class _BaselineImageSourceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.source: str | None = None

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        if tag.lower() == "img":
            self.source = dict(attrs).get("src")


@dataclass(frozen=True)
class BrandTextMatch:
    term: str
    text: str
    selector: str
    class_name: str

class BrandTextValidationStrategy:
    def find_matches(self, page: Page, terms: tuple[str, ...]) -> list[BrandTextMatch]:
        matches = page.evaluate(_FIND_TEXT_MATCHES_SCRIPT, list(terms))
        return [
            BrandTextMatch(
                term=match["term"],
                text=match["text"],
                selector=match["selector"],
                class_name=match["className"],
            )
            for match in matches
        ]


@dataclass(frozen=True)
class BrandVisualAsset:
    name: str
    selector: str | Locator
    baseline_path: Path


@dataclass(frozen=True)
class VisualValidationResult:
    name: str
    status: str
    detail: str


class ImageSimilarityValidationStrategy:
    def __init__(self, minimum_similarity: float = 90.0) -> None:
        if not 0 < minimum_similarity <= 100:
            raise ValueError("minimum_similarity must be greater than 0 and at most 100")
        self._minimum_similarity = minimum_similarity

    def compare(
        self,
        page: Page,
        asset: BrandVisualAsset,
        element_index: int = 0,
    ) -> VisualValidationResult:
        if not asset.baseline_path.is_file():
            return VisualValidationResult(asset.name, "skipped", "Baseline file is missing")

        matching_elements = (
            page.locator(asset.selector)
            if isinstance(asset.selector, str)
            else asset.selector
        )
        selector_description = (
            repr(asset.selector)
            if isinstance(asset.selector, str)
            else "provided locator"
        )
        if element_index < 0:
            return VisualValidationResult(
                asset.name,
                "failed",
                f"No page element at index {element_index} for {selector_description}",
            )
        locator = matching_elements.nth(element_index)
        try:
            locator.wait_for(state="attached")
        except PlaywrightTimeoutError:
            return VisualValidationResult(
                asset.name,
                "failed",
                f"No page element found at index {element_index} for "
                f"{selector_description}",
            )

        baseline = asset.baseline_path.read_bytes()
        baseline_mime = self._mime_type(asset.baseline_path)
        if (
            baseline_mime == "image/svg+xml"
            and baseline.lstrip().lower().startswith(b"<img")
        ):
            parser = _BaselineImageSourceParser()
            parser.feed(baseline.decode("utf-8"))
            if parser.source is None:
                return VisualValidationResult(
                    asset.name,
                    "failed",
                    "SVG baseline image markup does not contain an image source",
                )
            response = page.request.get(urljoin(page.url, parser.source))
            if not response.ok:
                return VisualValidationResult(
                    asset.name,
                    "failed",
                    f"Baseline image source returned HTTP {response.status}",
                )
            baseline = response.body()
            baseline_mime = response.headers.get("content-type", "").split(";", 1)[0]
            if not baseline_mime.startswith("image/"):
                return VisualValidationResult(
                    asset.name,
                    "failed",
                    f"Baseline image source returned unexpected content type {baseline_mime!r}",
                )

        element_info = locator.evaluate(
            """element => ({
                tagName: element.tagName.toLowerCase(),
                source: element instanceof HTMLImageElement
                    ? (element.currentSrc || element.src || element.getAttribute('src'))
                    : null,
                svgMarkup: element instanceof SVGSVGElement ? element.outerHTML : null,
                styles: element instanceof SVGSVGElement
                    ? Object.fromEntries(
                        ['color', 'fill', 'stroke', 'opacity', 'filter', 'visibility']
                            .map(name => [name, getComputedStyle(element).getPropertyValue(name)])
                    )
                    : null,
            })"""
        )
        if element_info["tagName"] == "svg":
            comparison = page.evaluate(
                _COMPARE_SVGS_SCRIPT,
                {
                    "actual": element_info["svgMarkup"],
                    "baseline": baseline.decode("utf-8"),
                    "styles": element_info["styles"],
                    "minimumSimilarity": self._minimum_similarity,
                },
            )
            return VisualValidationResult(
                asset.name,
                "passed" if comparison["matches"] else "failed",
                comparison["reason"],
            )
        elif element_info["source"]:
            source_url = urljoin(page.url, element_info["source"])
            response = page.request.get(source_url)
            if not response.ok:
                return VisualValidationResult(
                    asset.name,
                    "failed",
                    f"Image source returned HTTP {response.status}",
                )
            actual_image = response.body()
            actual_mime = response.headers.get("content-type", "").split(";", 1)[0]
            if not actual_mime.startswith("image/"):
                return VisualValidationResult(
                    asset.name,
                    "failed",
                    f"Image source returned unexpected content type {actual_mime!r}",
                )
            baseline_image = baseline
        else:
            return VisualValidationResult(
                asset.name,
                "failed",
                "Matched page element is neither an SVG nor an image with a source URL",
            )

        comparison = page.evaluate(
            _COMPARE_IMAGES_SCRIPT,
            {
                "actual": f"data:{actual_mime};base64,"
                + base64.b64encode(actual_image).decode("ascii"),
                "baseline": f"data:{baseline_mime};base64,"
                + base64.b64encode(baseline_image).decode("ascii"),
                "minimumSimilarity": self._minimum_similarity,
            },
        )
        return VisualValidationResult(
            asset.name,
            "passed" if comparison["matches"] else "failed",
            comparison["reason"],
        )

    @staticmethod
    def _mime_type(path: Path) -> str:
        return {
            ".png": "image/png",
            ".webp": "image/webp",
            ".svg": "image/svg+xml",
        }.get(path.suffix.lower(), "application/octet-stream")
