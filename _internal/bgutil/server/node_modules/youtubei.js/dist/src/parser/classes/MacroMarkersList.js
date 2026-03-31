import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import { Text } from '../misc.js';
import MacroMarkersInfoItem from './MacroMarkersInfoItem.js';
import MacroMarkersListItem from './MacroMarkersListItem.js';
export default class MacroMarkersList extends YTNode {
    static type = 'MacroMarkersList';
    contents;
    sync_button_label;
    constructor(data) {
        super();
        this.contents = Parser.parseArray(data.contents, [MacroMarkersInfoItem, MacroMarkersListItem]);
        this.sync_button_label = new Text(data.syncButtonLabel);
    }
}
//# sourceMappingURL=MacroMarkersList.js.map