import { useEffect, useRef, useState } from "react";
import * as pdfjsLib from "pdfjs-dist/legacy/build/pdf.mjs";
import workerUrl from "pdfjs-dist/legacy/build/pdf.worker.min.mjs?url";

// Worker self-hosted (bundled por Vite, SIN CDN — CLAUDE.md §10). El build "legacy" está
// transpilado para navegadores antiguos: por eso renderiza en móviles donde el <iframe> nativo
// dejaba el PDF en blanco.
pdfjsLib.GlobalWorkerOptions.workerSrc = workerUrl;

// Ancho de render mínimo: aunque el contenedor sea estrecho, renderizamos a esta resolución (x DPR)
// para que el PDF siga nítido al maximizar (el canvas se escala por CSS al ancho real).
const ANCHO_RENDER_MIN = 1100;

/**
 * Renderiza un PDF con PDF.js dentro de un <div> (canvas por página), en lugar de delegar en el
 * visor embebido del navegador (que muchos móviles no cargan dentro de un iframe). Lee el fichero
 * del origen sandbox (requiere CORS en esas respuestas, que son públicas).
 */
export function PdfViewer({ url, titulo }: { url: string; titulo: string }) {
  const contRef = useRef<HTMLDivElement>(null);
  const [estado, setEstado] = useState<"cargando" | "ok" | "error">("cargando");

  useEffect(() => {
    let cancelado = false;
    const cont = contRef.current;
    if (!cont) return;
    setEstado("cargando");

    (async () => {
      try {
        const doc = await pdfjsLib.getDocument({ url }).promise;
        if (cancelado) return;
        cont.replaceChildren();
        const dpr = Math.min(window.devicePixelRatio || 1, 2);
        const anchoCss = Math.max(cont.clientWidth || 800, ANCHO_RENDER_MIN);
        for (let n = 1; n <= doc.numPages; n++) {
          const page = await doc.getPage(n);
          if (cancelado) return;
          const base = page.getViewport({ scale: 1 });
          const viewport = page.getViewport({ scale: (anchoCss / base.width) * dpr });
          const canvas = document.createElement("canvas");
          canvas.className = "cms-pdf-page";
          canvas.width = Math.floor(viewport.width);
          canvas.height = Math.floor(viewport.height);
          const ctx = canvas.getContext("2d");
          if (!ctx) continue;
          cont.appendChild(canvas);
          await page.render({ canvasContext: ctx, viewport }).promise;
        }
        if (!cancelado) setEstado("ok");
      } catch {
        if (!cancelado) setEstado("error");
      }
    })();

    return () => {
      cancelado = true;
    };
  }, [url]);

  return (
    <div className="cms-pdf-viewer">
      <div ref={contRef} className="cms-pdf-pages" aria-label={`Documento PDF: ${titulo}`} />
      {estado === "cargando" && (
        <div className="cms-spinner" role="status" aria-label="Cargando el PDF" />
      )}
      {estado === "error" && (
        <p className="cms-muted" style={{ padding: "1rem" }}>
          No se ha podido mostrar el PDF aquí. Usa el botón <strong>Descargar / Imprimir</strong>
          {" "}para abrirlo.
        </p>
      )}
    </div>
  );
}
