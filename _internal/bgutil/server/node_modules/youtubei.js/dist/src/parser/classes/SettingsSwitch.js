import { YTNode } from '../helpers.js';
import NavigationEndpoint from './NavigationEndpoint.js';
import Text from './misc/Text.js';
export default class SettingsSwitch extends YTNode {
    static type = 'SettingsSwitch';
    title;
    subtitle;
    enabled;
    enable_endpoint;
    disable_endpoint;
    constructor(data) {
        super();
        this.title = new Text(data.title);
        this.subtitle = new Text(data.subtitle);
        this.enabled = data.enabled;
        this.enable_endpoint = new NavigationEndpoint(data.enableServiceEndpoint);
        this.disable_endpoint = new NavigationEndpoint(data.disableServiceEndpoint);
    }
}
//# sourceMappingURL=SettingsSwitch.js.map