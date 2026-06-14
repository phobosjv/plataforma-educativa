import { Node, mergeAttributes, type CommandProps } from "@tiptap/core";

// Nodo de bloque "figura con imagen" para el editor de artículos. Se serializa como
// <figure class="cms-fig cms-fig-{align} cms-fig-{size}"><img><figcaption>…</figcaption></figure>
// — etiquetas/clases que el sanitizador del servidor (nh3) ya permite (CLAUDE.md §10).
// El pie (figcaption) y la alineación/tamaño se guardan como atributos del nodo.

export type AlineacionImagen = "izquierda" | "centro" | "derecha";
export type TamanoImagen = "sm" | "md" | "lg" | "full";

const ALINEACIONES: AlineacionImagen[] = ["izquierda", "centro", "derecha"];
const TAMANOS: TamanoImagen[] = ["sm", "md", "lg", "full"];

export interface AtributosFigura {
  src: string;
  alt?: string;
  caption?: string;
  align?: AlineacionImagen;
  size?: TamanoImagen;
}

declare module "@tiptap/core" {
  interface Commands<ReturnType> {
    figuraImagen: {
      setFiguraImagen: (attrs: AtributosFigura) => ReturnType;
    };
  }
}

export const FiguraImagen = Node.create({
  name: "figuraImagen",
  group: "block",
  atom: true,
  draggable: true,
  selectable: true,

  addAttributes() {
    return {
      src: { default: "" },
      alt: { default: "" },
      caption: { default: "" },
      align: { default: "centro" as AlineacionImagen },
      size: { default: "md" as TamanoImagen },
    };
  },

  parseHTML() {
    return [
      {
        tag: "figure",
        getAttrs: (el): false | Record<string, unknown> => {
          const figura = el as HTMLElement;
          const img = figura.querySelector("img");
          if (!img) return false; // figuras sin imagen: no son este nodo
          const cls = figura.getAttribute("class") ?? "";
          const align = ALINEACIONES.find((a) => cls.includes(`cms-fig-${a}`)) ?? "centro";
          const size = TAMANOS.find((s) => cls.includes(`cms-fig-${s}`)) ?? "md";
          const fc = figura.querySelector("figcaption");
          return {
            src: img.getAttribute("src") ?? "",
            alt: img.getAttribute("alt") ?? "",
            caption: fc?.textContent ?? "",
            align,
            size,
          };
        },
      },
    ];
  },

  renderHTML({ node }) {
    const { src, alt, caption, align, size } = node.attrs as Required<AtributosFigura>;
    const clase = `cms-fig cms-fig-${align} cms-fig-${size}`;
    const hijos: unknown[] = [["img", mergeAttributes({ src, alt: alt || "" })]];
    if (caption) hijos.push(["figcaption", {}, caption]);
    return ["figure", mergeAttributes({ class: clase }), ...hijos] as never;
  },

  addCommands() {
    return {
      setFiguraImagen:
        (attrs: AtributosFigura) =>
        ({ commands }: CommandProps) =>
          commands.insertContent({
            type: this.name,
            attrs: {
              src: attrs.src,
              alt: attrs.alt ?? "",
              caption: attrs.caption ?? "",
              align: attrs.align ?? "centro",
              size: attrs.size ?? "md",
            },
          }),
    };
  },
});
