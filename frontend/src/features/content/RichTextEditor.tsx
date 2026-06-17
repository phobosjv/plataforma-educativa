import { useEditor, EditorContent, type Editor } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import Link from "@tiptap/extension-link";
import { useEffect, useRef, useState } from "react";
import { FiguraImagen, type AlineacionImagen, type TamanoImagen } from "./FiguraImagen";

// Editor WYSIWYG para artículos de texto. Emite HTML por onChange.
// El HTML se vuelve a sanear SIEMPRE en el servidor (nh3); aquí solo es edición.

function Boton({
  editor,
  activo,
  onClick,
  children,
  titulo,
  deshabilitado,
}: {
  editor: Editor;
  activo?: boolean;
  onClick: () => void;
  children: React.ReactNode;
  titulo: string;
  deshabilitado?: boolean;
}) {
  void editor; // re-render gobernado por el padre vía editor state
  return (
    <button
      type="button"
      className="cms-editor-btn"
      aria-pressed={activo}
      data-activo={activo ? "true" : undefined}
      disabled={deshabilitado}
      onMouseDown={(e) => e.preventDefault()}
      onClick={onClick}
      title={titulo}
    >
      {children}
    </button>
  );
}

const ALINEACIONES: { id: AlineacionImagen; icono: string; titulo: string }[] = [
  { id: "izquierda", icono: "⬅", titulo: "Alinear a la izquierda" },
  { id: "centro", icono: "⬛", titulo: "Centrar" },
  { id: "derecha", icono: "➡", titulo: "Alinear a la derecha" },
];

const TAMANOS: { id: TamanoImagen; etiqueta: string; titulo: string }[] = [
  { id: "sm", etiqueta: "S", titulo: "Pequeña" },
  { id: "md", etiqueta: "M", titulo: "Mediana" },
  { id: "lg", etiqueta: "L", titulo: "Grande" },
  { id: "full", etiqueta: "100%", titulo: "Ancho completo" },
];

export function RichTextEditor({
  value,
  onChange,
}: {
  value: string;
  onChange: (html: string) => void;
}) {
  const inputFichero = useRef<HTMLInputElement>(null);
  const [subiendo, setSubiendo] = useState(false);
  const [errorImg, setErrorImg] = useState<string | null>(null);

  const editor = useEditor({
    extensions: [
      StarterKit,
      Link.configure({
        openOnClick: false,
        autolink: true,
        // Los enlaces de artículos (incluidos perfiles de terceros / redes sociales) abren en una
        // pestaña nueva para no sacar al menor del sitio. El servidor (nh3) refuerza rel=noopener.
        HTMLAttributes: { target: "_blank", rel: "noopener noreferrer" },
      }),
      FiguraImagen,
    ],
    content: value,
    onUpdate: ({ editor }) => onChange(editor.getHTML()),
  });

  // Si el valor inicial llega de forma asíncrona (edición), sincronizar una vez.
  useEffect(() => {
    if (editor && value && editor.getHTML() !== value) {
      editor.commands.setContent(value, { emitUpdate: false });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [editor, value]);

  if (!editor) return null;

  function ponerEnlace() {
    const previo = editor!.getAttributes("link").href as string | undefined;
    const url = window.prompt("URL del enlace (vacío para quitar):", previo ?? "https://");
    if (url === null) return;
    if (url === "") {
      editor!.chain().focus().unsetLink().run();
      return;
    }
    editor!.chain().focus().setLink({ href: url }).run();
  }

  async function subirImagen(file: File) {
    setErrorImg(null);
    setSubiendo(true);
    try {
      const fd = new FormData();
      fd.append("fichero", file);
      const token = localStorage.getItem("auth_token");
      const r = await fetch("/api/v1/media/imagenes", {
        method: "POST",
        body: fd,
        headers: token ? { Authorization: `Bearer ${token}` } : undefined,
      });
      if (!r.ok) {
        const cuerpo = (await r.json().catch(() => null)) as { detail?: string } | null;
        throw new Error(cuerpo?.detail ?? "No se pudo subir la imagen.");
      }
      const { url } = (await r.json()) as { url: string };
      const alt = window.prompt("Texto alternativo (describe la imagen):", "") ?? "";
      editor!.chain().focus().setFiguraImagen({ src: url, alt }).run();
    } catch (e) {
      setErrorImg(e instanceof Error ? e.message : "Error al subir la imagen.");
    } finally {
      setSubiendo(false);
    }
  }

  function ponerPie() {
    const previo = (editor!.getAttributes("figuraImagen").caption as string) ?? "";
    const pie = window.prompt("Pie de imagen (vacío para quitar):", previo);
    if (pie === null) return;
    editor!.chain().focus().updateAttributes("figuraImagen", { caption: pie }).run();
  }

  const imagenSeleccionada = editor.isActive("figuraImagen");

  return (
    <div className="cms-editor">
      <div className="cms-editor-toolbar" role="toolbar" aria-label="Formato del texto">
        <Boton editor={editor} titulo="Negrita" activo={editor.isActive("bold")}
          onClick={() => editor.chain().focus().toggleBold().run()}><b>B</b></Boton>
        <Boton editor={editor} titulo="Cursiva" activo={editor.isActive("italic")}
          onClick={() => editor.chain().focus().toggleItalic().run()}><i>I</i></Boton>
        <Boton editor={editor} titulo="Tachado" activo={editor.isActive("strike")}
          onClick={() => editor.chain().focus().toggleStrike().run()}><s>S</s></Boton>
        <span className="cms-editor-sep" />
        <Boton editor={editor} titulo="Título" activo={editor.isActive("heading", { level: 2 })}
          onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}>H2</Boton>
        <Boton editor={editor} titulo="Subtítulo" activo={editor.isActive("heading", { level: 3 })}
          onClick={() => editor.chain().focus().toggleHeading({ level: 3 }).run()}>H3</Boton>
        <span className="cms-editor-sep" />
        <Boton editor={editor} titulo="Lista" activo={editor.isActive("bulletList")}
          onClick={() => editor.chain().focus().toggleBulletList().run()}>• Lista</Boton>
        <Boton editor={editor} titulo="Lista numerada" activo={editor.isActive("orderedList")}
          onClick={() => editor.chain().focus().toggleOrderedList().run()}>1. Lista</Boton>
        <Boton editor={editor} titulo="Cita" activo={editor.isActive("blockquote")}
          onClick={() => editor.chain().focus().toggleBlockquote().run()}>❝</Boton>
        <span className="cms-editor-sep" />
        <Boton editor={editor} titulo="Enlace" activo={editor.isActive("link")}
          onClick={ponerEnlace}>🔗</Boton>
        <Boton editor={editor} titulo="Insertar imagen" deshabilitado={subiendo}
          onClick={() => inputFichero.current?.click()}>{subiendo ? "⏳" : "🖼"}</Boton>
        <Boton editor={editor} titulo="Quitar formato"
          onClick={() => editor.chain().focus().clearNodes().unsetAllMarks().run()}>✕</Boton>
      </div>

      {/* Barra contextual de la imagen seleccionada: alineación, tamaño y pie */}
      {imagenSeleccionada && (
        <div className="cms-editor-toolbar" role="toolbar" aria-label="Opciones de la imagen">
          <span className="cms-muted" style={{ fontSize: ".8rem", marginRight: ".3rem" }}>Imagen:</span>
          {ALINEACIONES.map((a) => (
            <Boton key={a.id} editor={editor} titulo={a.titulo}
              activo={editor.isActive("figuraImagen", { align: a.id })}
              onClick={() => editor.chain().focus().updateAttributes("figuraImagen", { align: a.id }).run()}>
              {a.icono}
            </Boton>
          ))}
          <span className="cms-editor-sep" />
          {TAMANOS.map((t) => (
            <Boton key={t.id} editor={editor} titulo={t.titulo}
              activo={editor.isActive("figuraImagen", { size: t.id })}
              onClick={() => editor.chain().focus().updateAttributes("figuraImagen", { size: t.id }).run()}>
              {t.etiqueta}
            </Boton>
          ))}
          <span className="cms-editor-sep" />
          <Boton editor={editor} titulo="Pie de imagen" onClick={ponerPie}>📝 Pie</Boton>
          <Boton editor={editor} titulo="Eliminar imagen"
            onClick={() => editor.chain().focus().deleteSelection().run()}>🗑</Boton>
        </div>
      )}

      {errorImg && (
        <div className="cms-error" style={{ padding: ".4rem .75rem" }} role="alert">{errorImg}</div>
      )}

      <input
        ref={inputFichero}
        type="file"
        accept="image/png,image/jpeg,image/gif,image/webp"
        style={{ display: "none" }}
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) subirImagen(file);
          e.target.value = "";
        }}
      />

      <EditorContent editor={editor} className="cms-editor-area cms-prose" />
    </div>
  );
}
