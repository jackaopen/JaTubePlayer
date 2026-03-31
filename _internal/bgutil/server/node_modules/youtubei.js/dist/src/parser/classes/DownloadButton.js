import NavigationEndpoint from './NavigationEndpoint.js';
import { YTNode } from '../helpers.js';
export default class DownloadButton extends YTNode {
    static type = 'DownloadButton';
    style;
    size; // TODO: check this
    endpoint;
    target_id;
    constructor(data) {
        super();
        this.style = data.style;
        this.size = data.size;
        this.endpoint = new NavigationEndpoint(data.command);
        this.target_id = data.targetId;
    }
}
//# sourceMappingURL=DownloadButton.js.map