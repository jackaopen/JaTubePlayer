import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import DismissableDialogContentSection from './DismissableDialogContentSection.js';
export default class DismissableDialog extends YTNode {
    static type = 'DismissableDialog';
    title;
    sections;
    metadata;
    display_style;
    constructor(data) {
        super();
        this.title = data.title;
        this.sections = Parser.parseArray(data.sections, DismissableDialogContentSection);
        this.metadata = Parser.parseItem(data.metadata);
        this.display_style = data.displayStyle;
    }
}
//# sourceMappingURL=DismissableDialog.js.map