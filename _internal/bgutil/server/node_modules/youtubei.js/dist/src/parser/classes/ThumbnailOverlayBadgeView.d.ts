import type { ObservedArray } from '../helpers.js';
import { YTNode } from '../helpers.js';
import { type RawNode } from '../index.js';
import ThumbnailBadgeView from './ThumbnailBadgeView.js';
export default class ThumbnailOverlayBadgeView extends YTNode {
    static type: string;
    badges: ObservedArray<ThumbnailBadgeView>;
    position: string;
    constructor(data: RawNode);
}
