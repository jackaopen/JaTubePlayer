import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import ButtonView from './ButtonView.js';
export default class PanelFooterView extends YTNode {
    static type = 'PanelFooterView';
    primary_button;
    secondary_button;
    should_hide_divider;
    constructor(data) {
        super();
        this.primary_button = Parser.parseItem(data.primaryButton, ButtonView);
        this.secondary_button = Parser.parseItem(data.secondaryButton, ButtonView);
        this.should_hide_divider = !!data.shouldHideDivider;
    }
}
//# sourceMappingURL=PanelFooterView.js.map