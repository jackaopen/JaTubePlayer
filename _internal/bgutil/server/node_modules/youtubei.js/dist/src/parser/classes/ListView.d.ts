import type { ObservedArray } from '../helpers.js';
import type { RawNode } from '../types/RawResponse.js';
import { YTNode } from '../helpers.js';
import ListItemView from './ListItemView.js';
export default class ListView extends YTNode {
    static type: string;
    items: ObservedArray<ListItemView>;
    constructor(data: RawNode);
}
