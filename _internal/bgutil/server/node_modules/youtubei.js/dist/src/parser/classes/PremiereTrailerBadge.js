import { YTNode } from '../helpers.js';
import { Text } from '../misc.js';
export default class PremiereTrailerBadge extends YTNode {
    static type = 'PremiereTrailerBadge';
    label;
    constructor(data) {
        super();
        this.label = new Text(data.label);
    }
}
//# sourceMappingURL=PremiereTrailerBadge.js.map