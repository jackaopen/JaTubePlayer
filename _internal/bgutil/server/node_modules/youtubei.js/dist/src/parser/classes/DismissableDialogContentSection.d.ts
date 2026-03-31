import { YTNode } from '../helpers.js';
import type { RawNode } from '../index.js';
import Text from './misc/Text.js';
export default class DismissableDialogContentSection extends YTNode {
    static type: string;
    title: Text;
    subtitle: Text;
    constructor(data: RawNode);
}
