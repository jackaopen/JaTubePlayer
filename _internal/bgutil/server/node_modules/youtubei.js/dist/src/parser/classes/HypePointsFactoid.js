import { Parser } from '../index.js';
import { YTNode } from '../helpers.js';
import Factoid from './Factoid.js';
export default class HypePointsFactoid extends YTNode {
    static type = 'HypePointsFactoid';
    factoid;
    constructor(data) {
        super();
        this.factoid = Parser.parseItem(data.factoid, Factoid);
    }
}
//# sourceMappingURL=HypePointsFactoid.js.map