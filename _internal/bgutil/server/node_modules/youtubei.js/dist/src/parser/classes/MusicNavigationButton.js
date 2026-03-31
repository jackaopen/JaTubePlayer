import Text from './misc/Text.js';
import NavigationEndpoint from './NavigationEndpoint.js';
import { YTNode } from '../helpers.js';
export default class MusicNavigationButton extends YTNode {
    static type = 'MusicNavigationButton';
    button_text;
    endpoint;
    constructor(data) {
        super();
        this.button_text = new Text(data.buttonText).toString();
        this.endpoint = new NavigationEndpoint(data.clickCommand);
    }
}
//# sourceMappingURL=MusicNavigationButton.js.map