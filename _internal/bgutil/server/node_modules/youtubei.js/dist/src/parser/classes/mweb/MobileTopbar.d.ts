import type { ObservedArray } from '../../helpers.js';
import { YTNode } from '../../helpers.js';
import Text from '../misc/Text.js';
import { type RawNode } from '../../index.js';
export default class MobileTopbar extends YTNode {
    static type: string;
    placeholder_text: Text;
    buttons: ObservedArray<YTNode>;
    logo_type?: string;
    constructor(data: RawNode);
}
