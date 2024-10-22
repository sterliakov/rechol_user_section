function renderPdfEditor(
	{ initColorPicker, csrfmiddlewaretoken, workerSrc, documentId },
	urls,
) {
	const PDFJSAnnotate = PDFAnnotate.default;

	const REGEXP = /[xy]/g;
	const PATTERN = "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx";

	const replacement = (c) => {
		const r = (Math.random() * 16) | 0;
		const v = c === "x" ? r : (r & 0x3) | 0x8;
		return v.toString(16);
	};
	const uuid = () => PATTERN.replace(REGEXP, replacement);

	class MyStoreAdapter extends PDFJSAnnotate.StoreAdapter {
		async __getAnnotations(documentId, pageNumber) {
			const uri = new URL(urls.listAnnotations, window.location.origin);
			uri.searchParams.set("filename", documentId);
			if (pageNumber != null) uri.searchParams.set("page", pageNumber);
			const ann = await $.get(uri);
			const annotations = ann
				.map((a) => {
					a.annotation = JSON.parse(a.annotation);
					return a;
				})
				.filter((a) => pageNumber == null || a.page === pageNumber)
				.map((a) => {
					const t = a.annotation;
					t.page = a.page;
					t.uuid = a.annotation_id;
					return t;
				});

			return {
				documentId,
				pageNumber,
				annotations,
			};
		}
		async getAnnotation(documentId, annotationId) {
			const rsp = await this.getAnnotations(documentId, null);
			return rsp.annotations.filter((a) => a.uuid === annotationId)[0];
		}
		async __addAnnotation(documentId, pageNumber, annotation) {
			const uuid_ = uuid();
			await $.post(urls.listAnnotations, {
				filename: documentId,
				annotation_id: uuid_,
				page: pageNumber,
				annotation: JSON.stringify(annotation),
				csrfmiddlewaretoken,
			});

			annotation.uuid = uuid_;
			annotation.page = pageNumber;
			return annotation;
		}
		async __editAnnotation(documentId, annotationId, annotation) {
			await $.post({
				url: urls.annotationDetail.replace("__unknown__", annotationId),
				method: "PUT",
				data: JSON.stringify({
					filename: documentId,
					annotation_id: annotationId,
					page: annotation.page,
					annotation: JSON.stringify(annotation),
					csrfmiddlewaretoken,
				}),
				contentType: "application/json; utf8",
				headers: { "X-CSRFToken": csrfmiddlewaretoken },
				dataType: "json",
				processData: false,
			});
			return annotation;
		}
		async __deleteAnnotation(documentId, annotationId) {
			await $.post({
				url: urls.annotationDetail.replace("__unknown__", annotationId),
				method: "DELETE",
				headers: { "X-CSRFToken": csrfmiddlewaretoken },
			});
			return true;
		}
		async getComments(documentId, annotationId) {
			return [];
		}
		async __addComment(documentId, annotationId, content) {
			throw new Error("Not implemented!");
		}
		async __deleteComment(documentId, commentId) {
			throw new Error("Not implemented!");
		}
	}

	window.ad = new MyStoreAdapter();
	function htmlEscape(text) {
		return text
			.replace("&", "&amp;")
			.replace(">", "&gt;")
			.replace("<", "&lt;")
			.replace('"', "&quot;")
			.replace("'", "&#39;");
	}

	const { UI } = PDFJSAnnotate;
	let PAGE_HEIGHT;
	const RENDER_OPTIONS = {
		documentId,
		pdfDocument: null,
		scale:
			Number.parseFloat(localStorage.getItem(`${documentId}/scale`), 10) ||
			1.33,
		rotate:
			Number.parseInt(localStorage.getItem(`${documentId}/rotate`), 10) || 0,
	};

	PDFJSAnnotate.setStoreAdapter(new MyStoreAdapter());
	pdfjsLib.GlobalWorkerOptions.workerSrc = workerSrc;

	// Render stuff
	let NUM_PAGES = 0;
	const renderedPages = [];
	let okToRender = false;
	document.getElementById("content-wrapper").addEventListener("scroll", (e) => {
		const visiblePageNum = Math.round(e.target.scrollTop / PAGE_HEIGHT) + 1;
		const visiblePage = document.querySelector(
			`.page[data-page-number="${visiblePageNum}"][data-loaded="false"]`,
		);

		if (renderedPages.indexOf(visiblePageNum) === -1) {
			okToRender = true;
			renderedPages.push(visiblePageNum);
		} else {
			okToRender = false;
		}

		if (visiblePage && okToRender) {
			setTimeout(() => {
				UI.renderPage(visiblePageNum, RENDER_OPTIONS);
			});
		}
	});

	function render() {
		const loadingTask = pdfjsLib.getDocument({
			url: RENDER_OPTIONS.documentId,
			cMapUrl: urls.cMaps,
			cMapPacked: true,
		});

		loadingTask.promise.then((pdf) => {
			RENDER_OPTIONS.pdfDocument = pdf;

			const viewer = document.getElementById("viewer");
			viewer.innerHTML = "";
			NUM_PAGES = pdf.numPages;
			for (let i = 0; i < NUM_PAGES; i++) {
				const page = UI.createPage(i + 1);
				viewer.appendChild(page);
			}

			UI.renderPage(1, RENDER_OPTIONS).then(([pdfPage, annotations]) => {
				const viewport = pdfPage.getViewport({
					scale: RENDER_OPTIONS.scale,
					rotation: RENDER_OPTIONS.rotate,
				});
				PAGE_HEIGHT = viewport.height;
			});
		});
	}
	render();

	// Hotspot color stuff
	(() => {
		let hotspotColor =
			localStorage.getItem(`${RENDER_OPTIONS.documentId}/hotspot/color`) ||
			"darkgoldenrod";
		let currentTarget;

		function handleAnnotationClick(target) {
			const type = target.getAttribute("data-pdf-annotate-type");
			if (["fillcircle", "arrow"].indexOf(type) === -1) {
				return; // nothing to do
			}
			currentTarget = target;
			hotspotColor = currentTarget.getAttribute("stroke");

			UI.setArrow(10, hotspotColor);
			UI.setCircle(10, hotspotColor);

			const a = document.querySelector(".hotspot-color .color");
			if (a) {
				a.setAttribute("data-color", hotspotColor);
				a.style.background = hotspotColor;
			}
		}

		function handleAnnotationBlur(target) {
			if (currentTarget === target) {
				currentTarget = undefined;
			}
		}

		initColorPicker(
			document.querySelector(".hotspot-color"),
			hotspotColor,
			(value) => {
				if (value === hotspotColor) {
					return; // nothing to do
				}
				localStorage.setItem(
					`${RENDER_OPTIONS.documentId}/hotspot/color`,
					value,
				);
				hotspotColor = value;

				UI.setArrow(10, hotspotColor);
				UI.setCircle(10, hotspotColor);

				if (!currentTarget) {
					return; // nothing to do
				}

				const type = currentTarget.getAttribute("data-pdf-annotate-type");
				const annotationId = currentTarget.getAttribute("data-pdf-annotate-id");
				if (["fillcircle", "arrow"].indexOf(type) === -1) {
					return; // nothing to do
				}

				// update target
				currentTarget.setAttribute("stroke", hotspotColor);
				currentTarget.setAttribute("fill", hotspotColor);

				// update annotation
				PDFJSAnnotate.getStoreAdapter()
					.getAnnotation(documentId, annotationId)
					.then((annotation) => {
						annotation.color = hotspotColor;
						PDFJSAnnotate.getStoreAdapter().editAnnotation(
							documentId,
							annotationId,
							annotation,
						);
					});
			},
		);

		UI.addEventListener("annotation:click", handleAnnotationClick);
		UI.addEventListener("annotation:blur", handleAnnotationBlur);
	})();

	// Text stuff
	(() => {
		let textSize;
		let textColor;

		function initText() {
			const size = document.querySelector(".toolbar .text-size");
			[8, 9, 10, 11, 12, 14, 18, 24, 30, 36, 48, 60, 72, 96].forEach((s) => {
				size.appendChild(new Option(s, s));
			});

			setText(
				localStorage.getItem(`${RENDER_OPTIONS.documentId}/text/size`) || 12,
				localStorage.getItem(`${RENDER_OPTIONS.documentId}/text/color`) ||
					"#000000",
			);

			initColorPicker(
				document.querySelector(".text-color"),
				textColor,
				(value) => {
					setText(textSize, value);
				},
			);
		}

		function setText(size, color) {
			let modified = false;

			if (textSize !== size) {
				modified = true;
				textSize = size;
				localStorage.setItem(
					`${RENDER_OPTIONS.documentId}/text/size`,
					textSize,
				);
				document.querySelector(".toolbar .text-size").value = textSize;
			}

			if (textColor !== color) {
				modified = true;
				textColor = color;
				localStorage.setItem(
					`${RENDER_OPTIONS.documentId}/text/color`,
					textColor,
				);

				let selected = document.querySelector(
					".toolbar .text-color.color-selected",
				);
				if (selected) {
					selected.classList.remove("color-selected");
					selected.removeAttribute("aria-selected");
				}

				selected = document.querySelector(
					`.toolbar .text-color[data-color="${color}"]`,
				);
				if (selected) {
					selected.classList.add("color-selected");
					selected.setAttribute("aria-selected", true);
				}
			}

			if (modified) {
				UI.setText(textSize, textColor);
			}
		}

		function handleTextSizeChange(e) {
			setText(e.target.value, textColor);
		}

		document
			.querySelector(".toolbar .text-size")
			.addEventListener("change", handleTextSizeChange);

		initText();
	})();

	// Pen stuff
	(() => {
		let penSize;
		let penColor;

		function initPen() {
			const size = document.querySelector(".toolbar .pen-size");
			for (let i = 0; i < 20; i++) {
				size.appendChild(new Option(i + 1, i + 1));
			}

			setPen(
				localStorage.getItem(`${RENDER_OPTIONS.documentId}/pen/size`) || 1,
				localStorage.getItem(`${RENDER_OPTIONS.documentId}/pen/color`) ||
					"#000000",
			);

			initColorPicker(
				document.querySelector(".pen-color"),
				penColor,
				(value) => {
					setPen(penSize, value);
				},
			);
		}

		function setPen(size, color) {
			let modified = false;

			if (penSize !== size) {
				modified = true;
				penSize = size;
				localStorage.setItem(`${RENDER_OPTIONS.documentId}/pen/size`, penSize);
				document.querySelector(".toolbar .pen-size").value = penSize;
			}

			if (penColor !== color) {
				modified = true;
				penColor = color;
				localStorage.setItem(
					`${RENDER_OPTIONS.documentId}/pen/color`,
					penColor,
				);

				let selected = document.querySelector(
					".toolbar .pen-color.color-selected",
				);
				if (selected) {
					selected.classList.remove("color-selected");
					selected.removeAttribute("aria-selected");
				}

				selected = document.querySelector(
					`.toolbar .pen-color[data-color="${color}"]`,
				);
				if (selected) {
					selected.classList.add("color-selected");
					selected.setAttribute("aria-selected", true);
				}
			}

			if (modified) {
				UI.setPen(penSize, penColor);
			}
		}

		function handlePenSizeChange(e) {
			setPen(e.target.value, penColor);
		}

		document
			.querySelector(".toolbar .pen-size")
			.addEventListener("change", handlePenSizeChange);

		initPen();
	})();

	// Toolbar buttons
	(() => {
		let tooltype =
			localStorage.getItem(`${RENDER_OPTIONS.documentId}/tooltype`) || "cursor";
		if (tooltype) {
			setActiveToolbarItem(
				tooltype,
				document.querySelector(`.toolbar button[data-tooltype=${tooltype}]`),
			);
		}

		function setActiveToolbarItem(type, button) {
			const active = document.querySelector(".toolbar button.active");
			if (active) {
				active.classList.remove("active");

				switch (tooltype) {
					case "cursor":
						UI.disableEdit();
						break;
					case "eraser":
						UI.disableEraser();
						break;
					case "draw":
						UI.disablePen();
						break;
					case "arrow":
						UI.disableArrow();
						break;
					case "text":
						UI.disableText();
						break;
					case "point":
						UI.disablePoint();
						break;
					case "area":
					case "highlight":
					case "strikeout":
						UI.disableRect();
						break;
					case "circle":
					case "emptycircle":
					case "fillcircle":
						UI.disableCircle();
						break;
				}
			}

			if (button) {
				button.classList.add("active");
			}
			if (tooltype !== type) {
				localStorage.setItem(`${RENDER_OPTIONS.documentId}/tooltype`, type);
			}
			tooltype = type;

			switch (type) {
				case "cursor":
					UI.enableEdit();
					break;
				case "eraser":
					UI.enableEraser();
					break;
				case "draw":
					UI.enablePen();
					break;
				case "arrow":
					UI.enableArrow();
					break;
				case "text":
					UI.enableText();
					break;
				case "point":
					UI.enablePoint();
					break;
				case "area":
				case "highlight":
				case "strikeout":
					UI.enableRect(type);
					break;
				case "circle":
				case "emptycircle":
				case "fillcircle":
					UI.enableCircle(type);
					break;
			}
		}

		function handleToolbarClick(e) {
			if (e.target.nodeName === "BUTTON") {
				setActiveToolbarItem(e.target.getAttribute("data-tooltype"), e.target);
			}
		}

		document
			.querySelector(".toolbar")
			.addEventListener("click", handleToolbarClick);
	})();

	// Scale/rotate
	(() => {
		function setScaleRotate(scale, rotate) {
			scale = Number.parseFloat(scale, 10);
			rotate = Number.parseInt(rotate, 10);

			if (RENDER_OPTIONS.scale !== scale || RENDER_OPTIONS.rotate !== rotate) {
				RENDER_OPTIONS.scale = scale;
				RENDER_OPTIONS.rotate = rotate;

				localStorage.setItem(
					`${RENDER_OPTIONS.documentId}/scale`,
					RENDER_OPTIONS.scale,
				);
				localStorage.setItem(
					`${RENDER_OPTIONS.documentId}/rotate`,
					RENDER_OPTIONS.rotate % 360,
				);

				render();
			}
		}

		function handleScaleChange(e) {
			setScaleRotate(e.target.value, RENDER_OPTIONS.rotate);
		}

		function handleRotateCWClick() {
			setScaleRotate(RENDER_OPTIONS.scale, RENDER_OPTIONS.rotate + 90);
		}

		function handleRotateCCWClick() {
			setScaleRotate(RENDER_OPTIONS.scale, RENDER_OPTIONS.rotate - 90);
		}

		document.querySelector(".toolbar select.scale").value =
			RENDER_OPTIONS.scale;
		document
			.querySelector(".toolbar select.scale")
			.addEventListener("change", handleScaleChange);
		document
			.querySelector(".toolbar .rotate-ccw")
			.addEventListener("click", handleRotateCCWClick);
		document
			.querySelector(".toolbar .rotate-cw")
			.addEventListener("click", handleRotateCWClick);
	})();

	// Clear toolbar button
	(() => {
		function handleClearClick(e) {
			if (confirm("Are you sure you want to clear annotations?")) {
				for (let i = 0; i < NUM_PAGES; i++) {
					document.querySelector(
						`div#pageContainer${i + 1} svg.annotationLayer`,
					).innerHTML = "";
				}

				localStorage.removeItem(`${RENDER_OPTIONS.documentId}/annotations`);
			}
		}
		document
			.querySelector("a.clear")
			.addEventListener("click", handleClearClick);
	})();
}
