import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import DialogHeaderView from './DialogHeaderView.js';
import FormFooterView from './FormFooterView.js';
import CreatePlaylistDialogFormView from './CreatePlaylistDialogFormView.js';
import ListView from './ListView.js';
import PanelFooterView from './PanelFooterView.js';
export default class DialogView extends YTNode {
    static type = 'DialogView';
    header;
    footer;
    custom_content;
    constructor(data) {
        super();
        this.header = Parser.parseItem(data.header, DialogHeaderView);
        this.footer = Parser.parseItem(data.footer, [FormFooterView, PanelFooterView]);
        this.custom_content = Parser.parseItem(data.customContent, [CreatePlaylistDialogFormView, ListView]);
    }
}
//# sourceMappingURL=DialogView.js.map