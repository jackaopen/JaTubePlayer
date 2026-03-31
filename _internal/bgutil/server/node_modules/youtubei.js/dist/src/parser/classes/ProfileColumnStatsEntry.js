import Text from './misc/Text.js';
import { YTNode } from '../helpers.js';
export default class ProfileColumnStatsEntry extends YTNode {
    static type = 'ProfileColumnStatsEntry';
    label;
    value;
    constructor(data) {
        super();
        this.label = new Text(data.label);
        this.value = new Text(data.value);
    }
}
//# sourceMappingURL=ProfileColumnStatsEntry.js.map