import { YTNode } from '../helpers.js';
import type { RawNode } from '../index.js';
import Text from './misc/Text.js';
export default class SectionHeaderView extends YTNode {
    static type: string;
    headline: Text;
    constructor(data: RawNode);
}
