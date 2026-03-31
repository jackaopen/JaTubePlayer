import Text from './misc/Text.js';
import { YTNode } from '../helpers.js';
export default class Alert extends YTNode {
    static type = 'Alert';
    text;
    alert_type;
    constructor(data) {
        super();
        this.text = new Text(data.text);
        this.alert_type = data.type;
    }
}
//# sourceMappingURL=Alert.js.map