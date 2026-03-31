import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import Factoid from './Factoid.js';
export default class UploadTimeFactoid extends YTNode {
    static type = 'UploadTimeFactoid';
    factoid;
    constructor(data) {
        super();
        this.factoid = Parser.parseItem(data.factoid, Factoid);
    }
}
//# sourceMappingURL=UploadTimeFactoid.js.map