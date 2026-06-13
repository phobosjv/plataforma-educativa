import { useEditor, EditorContent, type Editor } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import Link from "@tiptap/extension-link";
import { useEffect } from "react";

// Editor WYSIWYG para artículos de texto. Emite HTML por onChange.
// El HTML se vuelve a sanear SIEMPRE en el servidor (nh3); aquí solo es edición.

function Boton({
  editor,
  activo,
  onClick,
  children,
  titulo,
}: {
  editor: Editor;
  activo?: boolean;
  onClick: () => void;
  children: React.ReactNode;
  titulo: string;
}) {
  void editor; // re-render gobernado por el padre vía editor state
  return (
    <button
      type="button"
      className="cms-editor-btn"
      aria-pressed={activo}
      data-activo={activo ? "true" : undefined}
      onMouseDown={(e) => e.preventDefault()}
      onClick={onClick}
      title={titulo}
    >
      {children}
    </button>
  );
}

export function RichTextEditor({
  value,
  onChange,
}: {
  value: string;
  onChange: (html: string) => void;
}) {
  const editor = useEditor({
    extensions: [
      StarterKit,
      Link.configure({ openOnClick: false, autolink: true }),
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
        <Boton editor={editor} titulo="Quitar formato"
          onClick={() => editor.chain().focus().clearNodes().unsetAllMarks().run()}>✕</Boton>
      </div>
      <EditorContent editor={editor} className="cms-editor-area cms-prose" />
    </div>
  );
}
