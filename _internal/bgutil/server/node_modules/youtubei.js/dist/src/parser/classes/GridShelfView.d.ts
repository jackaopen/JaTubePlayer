import type { ObservedArray } from '../helpers.js';
import { YTNode } from '../helpers.js';
import { type RawNode } from '../index.js';
import ButtonView from './ButtonView.js';
export default class GridShelfView extends YTNode {
    static type: string;
    contents: ObservedArray<YTNode>;
    header: YTNode | null;
    content_aspect_ratio: string;
    enable_vertical_expansion: boolean;
    show_more_button: ButtonView | null;
    show_less_button: ButtonView | null;
    min_collapsed_item_count: number;
    constructor(data: RawNode);
}
