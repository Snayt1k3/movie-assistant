import { z } from "zod"
import { getJson } from "./client"
import type { ApiResult } from "./result"
import type { LibraryPage } from "./types"

const TitleShortSchema = z.object({
    id: z.number(),
    type: z.enum(["movie", "show"]),
    category: z.enum(["film", "series", "anime"]),
    title_ru: z.string(),
    title_orig: z.string().nullable(),
    slug: z.string().nullable(),
    year: z.number().nullable(),
    status: z.enum(["announced", "ongoing", "ended", "released", "canceled"]),
    poster_path: z.string().nullable(),
    episodes_total: z.number().nullable()
})

const LibraryItemSchema = z.object({
    title: TitleShortSchema,
    status: z.enum(["planned", "on_hold", "watching", "completed", "dropped"]),
    rating: z.number().nullable(),
    is_favorite: z.boolean(),
    episodes_watched: z.number(),
    rewatch_count: z.number(),
    started_at: z.string().nullable(),
    finished_at: z.string().nullable(),
    updated_at: z.string(),
})

export const LibraryPageSchema = z.object({
    items: z.array(LibraryItemSchema),
    has_more: z.boolean(),
}) satisfies z.ZodType<LibraryPage>;

export async function getLibrary(userRef: string, offset = 0): Promise<ApiResult<LibraryPage>> {
    const r = await getJson(`/api/v1/users/${userRef}/library?limit=20&offset=${offset}`);
  if (r.kind === "error") {
    return r;
  }
  const parsed = LibraryPageSchema.safeParse(r.data);

  if (parsed.success) {
    return { kind: "ok", data: parsed.data };
  }
  return { kind: "error", message: JSON.stringify(parsed.error.issues) };

}