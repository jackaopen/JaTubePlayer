import { YTNode } from '../helpers.js';
import NavigationEndpoint from './NavigationEndpoint.js';
import Text from './misc/Text.js';
export default class DidYouMean extends YTNode {
    static type = 'DidYouMean';
    text;
    corrected_query;
    endpoint;
    constructor(data) {
        super();
        this.text = new Text(data.didYouMean).toString();
        this.corrected_query = new Text(data.correctedQuery);
        this.endpoint = new NavigationEndpoint(data.navigationEndpoint || data.correctedQueryEndpoint);
    }
}
//# sourceMappingURL=DidYouMean.js.map