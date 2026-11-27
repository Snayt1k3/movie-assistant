import type { components } from "./schema";

type S = components["schemas"];


export type LibraryItem = S["LibraryItemOut"];
export type LibraryStatus = S["LibraryStatus"];
export type LibraryPage = S["Page_LibraryItemOut_"]

export type TokenPair = S["TokenPair"];
export type RegisterIn = S["RegisterIn"]