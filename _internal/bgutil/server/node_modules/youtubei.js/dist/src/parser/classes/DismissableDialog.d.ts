import { type ObservedArray, YTNode } from '../helpers.js';
import { type RawNode } from '../index.js';
import DismissableDialogContentSection from './DismissableDialogContentSection.js';
export default class DismissableDialog extends YTNode {
    static type: string;
    title: string;
    sections: ObservedArray<DismissableDialogContentSection>;
    metadata: YTNode | null;
    display_style: string;
    constructor(data: RawNode);
}
