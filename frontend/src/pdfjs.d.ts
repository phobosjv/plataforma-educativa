// El build "legacy" de pdfjs-dist (transpilado para máxima compatibilidad de navegador, incl.
// móviles antiguos) no expone tipos en su subruta de exports. Reusamos los del paquete principal.
declare module "pdfjs-dist/legacy/build/pdf.mjs" {
  export * from "pdfjs-dist";
}
