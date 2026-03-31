import { YTNode } from '../helpers.js';
import NavigationEndpoint from './NavigationEndpoint.js';
import Text from './misc/Text.js';
export default class SettingBoolean extends YTNode {
    static type = 'SettingBoolean';
    title;
    summary;
    enable_endpoint;
    disable_endpoint;
    item_id;
    constructor(data) {
        super();
        if (Reflect.has(data, 'title')) {
            this.title = new Text(data.title);
        }
        if (Reflect.has(data, 'summary')) {
            this.summary = new Text(data.summary);
        }
        if (Reflect.has(data, 'enableServiceEndpoint')) {
            this.enable_endpoint = new NavigationEndpoint(data.enableServiceEndpoint);
        }
        if (Reflect.has(data, 'disableServiceEndpoint')) {
            this.disable_endpoint = new NavigationEndpoint(data.disableServiceEndpoint);
        }
        this.item_id = data.itemId;
    }
}
//# sourceMappingURL=SettingBoolean.js.map