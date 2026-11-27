import { useEffect, useState } from "react";
import { getLibrary } from "../../api/library";
import type { LibraryPage } from "../../api/types";
import { itemLabel, statusLabels } from "./labels";


type State = 
    | { kind: "loading"}
    | { kind: "error", message: string}
    | { kind: "ready", page: LibraryPage}


type Props = { userRef: string}

export function LibraryList({ userRef }: Props) {
  const [state, setState] = useState<State>({ kind: "loading" });

  useEffect(() => {
    let cancelled = false;
    getLibrary(userRef).then((r) => {
      if (cancelled) return;
      setState(
        r.kind === "ok"
          ? { kind: "ready", page: r.data }
          : { kind: "error", message: r.message },
      );
    });
    return () => {
      cancelled = true;
    };
  }, [userRef]);

  switch (state.kind) {
    case "loading":
      return <p>Загрузка…</p>;
    case "error":
      return <p>Ошибка: {state.message}</p>;
    case "ready":
      if (state.page.items.length === 0) {
        return <p>Библиотека пуста</p>;
      }
      return (
        <ul>
          {state.page.items.map((item) => (
            <li key={item.title.id}>
              {itemLabel(item)} — {statusLabels[item.status]}
            </li>
          ))}
        </ul>
      );
  }
}