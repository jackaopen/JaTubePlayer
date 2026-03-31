import { YTNode } from '../helpers.js';
import Text from './misc/Text.js';
export default class AttributionView extends YTNode {
    static type = 'AttributionView';
    text;
    suffix;
    constructor(data) {
        super();
        this.text = Text.fromAttributed(data.text);
        this.suffix = Text.fromAttributed(data.suffix);
    }
}
//# sourceMappingURL=AttributionView.js.map