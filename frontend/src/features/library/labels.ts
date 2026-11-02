import type { LibraryItem, LibraryStatus } from "../../api/types";

export const statusLabels: Record<LibraryStatus, string> = {
    "completed": "Завершенное",
    "dropped": "Брошенное",
    "on_hold": "На удержание",
    "planned": "Запланированное",
    "watching": "Смотрю",
}

export function itemLabel(item: LibraryItem): string {
    const rating = item.rating === null ? "без оценки" : `оценка ${item.rating}`;
    return `${item.title.title_ru} (${item.title.year ?? '-' }) - ${rating}`
}