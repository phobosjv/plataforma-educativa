import { useEffect } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../../shared/api/client";
import type { components } from "../../shared/api/schema";
import {
  PALETAS_PREDEFINIDAS,
  aplicarPaleta,
  resolverPaleta,
  type Palette,
} from "./palettes";
import { aplicarFuente } from "./fonts";
import { aplicarFondo } from "./backgrounds";

type ConfigDTO = components["schemas"]["ConfiguracionResponse"];
type PaletaDTO = components["schemas"]["PaletaResponse"];
type AjustesGenerales = components["schemas"]["AjustesGeneralesRequest"];
type Donacion = components["schemas"]["DonacionResponse"];

function toFrontendPalette(p: PaletaDTO): Palette {
  return {
    id: p.id,
    nombre: p.nombre,
    predefinida: false,
    emoji: "🎨",
    colores: { bg: p.bg, surface: p.surface, fg: p.fg, primary: p.primary },
  };
}

function fetchConfig(): Promise<ConfigDTO> {
  return api
    .GET("/api/v1/config/")
    .then(({ data, error }) => {
      if (error) throw error;
      return data!;
    });
}

export function useConfig() {
  const { data, isLoading } = useQuery<ConfigDTO>({
    queryKey: ["site-config"],
    queryFn: fetchConfig,
    staleTime: 60_000,
  });

  useEffect(() => {
    if (!data) return;
    const personalizadas = data.paletas_personalizadas.map(toFrontendPalette);
    const colores = resolverPaleta(data.paleta_activa, personalizadas);
    aplicarPaleta(colores);
    aplicarFuente(data.fuente_activa);
    aplicarFondo(data.fondo_activo, data.fondo_estilo);
  }, [data]);

  const personalizadas = (data?.paletas_personalizadas ?? []).map(toFrontendPalette);
  const todasLasPaletas: Palette[] = [...PALETAS_PREDEFINIDAS, ...personalizadas];

  return {
    config: data,
    isLoading,
    nombre_sitio: data?.nombre_sitio ?? "Plataforma Educativa",
    paleta_activa: data?.paleta_activa ?? "cielo",
    fuente_activa: data?.fuente_activa ?? "sistema",
    fondo_activo: data?.fondo_activo ?? "ninguno",
    fondo_estilo: data?.fondo_estilo ?? "ordenado",
    logo_url: data?.logo_url ?? "",
    aula_abierta_label: data?.aula_abierta_label ?? "Aula Abierta",
    aula_abierta_emoji: data?.aula_abierta_emoji ?? "🌟",
    catalogo_titulo: data?.catalogo_titulo ?? "¿En qué curso estás?",
    catalogo_subtitulo: data?.catalogo_subtitulo ?? "Toca tu curso para ver las actividades",
    donaciones: (data?.donaciones ?? []) as Donacion[],
    publicidad_activa: data?.publicidad_activa ?? false,
    publicidad_html_izquierda: data?.publicidad_html_izquierda ?? "",
    publicidad_html_derecha: data?.publicidad_html_derecha ?? "",
    todasLasPaletas,
    personalizadas,
  };
}

// Extrae un mensaje legible del error que devuelve openapi-fetch.
function mensajeError(error: unknown): string {
  if (error && typeof error === "object" && "detail" in error) {
    const d = (error as { detail: unknown }).detail;
    if (typeof d === "string") return d;
  }
  return "No se pudo completar la operación. Inténtalo de nuevo.";
}

export function useConfigMutations() {
  const qc = useQueryClient();
  const invalidate = () => qc.invalidateQueries({ queryKey: ["site-config"] });

  async function guardarAjustesGenerales(ajustes: AjustesGenerales) {
    const { data, error } = await api.PUT("/api/v1/config/general", { body: ajustes });
    if (error || !data) throw new Error(mensajeError(error));
    aplicarFuente(data.fuente_activa);
    aplicarFondo(data.fondo_activo, data.fondo_estilo);
    invalidate();
  }

  async function activarPaleta(paleta_id: string) {
    const { data, error } = await api.PUT("/api/v1/config/paleta", {
      body: { paleta_id },
    });
    if (error || !data) throw new Error(mensajeError(error));
    const personalizadas = data.paletas_personalizadas.map(toFrontendPalette);
    aplicarPaleta(resolverPaleta(data.paleta_activa, personalizadas));
    invalidate();
  }

  async function agregarPaleta(p: Omit<Palette, "predefinida" | "emoji">) {
    const { error } = await api.POST("/api/v1/config/paletas", {
      body: { id: p.id, nombre: p.nombre, ...p.colores },
    });
    if (error) throw new Error(mensajeError(error));
    invalidate();
  }

  async function eliminarPaleta(paleta_id: string) {
    const { error } = await api.DELETE("/api/v1/config/paletas/{paleta_id}", {
      params: { path: { paleta_id } },
    });
    if (error) throw new Error(mensajeError(error));
    invalidate();
  }

  return { guardarAjustesGenerales, activarPaleta, agregarPaleta, eliminarPaleta };
}
