import { YTNode } from '../helpers.js';
import Text from './misc/Text.js';
export default class DismissableDialogContentSection extends YTNode {
    static type = 'DismissableDialogContentSection';
    title;
    subtitle;
    constructor(data) {
        super();
        this.title = new Text(data.title);
        this.subtitle = new Text(data.subtitle);
    }
}
//# sourceMappingURL=DismissableDialogContentSection.js.map