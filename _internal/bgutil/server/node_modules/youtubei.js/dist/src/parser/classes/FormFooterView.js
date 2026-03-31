import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import PanelFooterView from './PanelFooterView.js';
export default class FormFooterView extends YTNode {
    static type = 'FormFooterView';
    panel_footer;
    form_id;
    container_type;
    constructor(data) {
        super();
        this.panel_footer = Parser.parseItem(data.panelFooter, PanelFooterView);
        this.form_id = data.formId;
        this.container_type = data.containerType;
    }
}
//# sourceMappingURL=FormFooterView.js.map