import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import Factoid from './Factoid.js';
export default class ViewCountFactoid extends YTNode {
    static type = 'ViewCountFactoid';
    view_count_entity_key;
    factoid;
    view_count_type;
    constructor(data) {
        super();
        this.view_count_entity_key = data.viewCountEntityKey;
        this.factoid = Parser.parseItem(data.factoid, [Factoid]);
        this.view_count_type = data.viewCountType;
    }
}
//# sourceMappingURL=ViewCountFactoid.js.map