import { YTNode } from '../helpers.js';
import Text from './misc/Text.js';
export default class MusicCardShelfHeaderBasic extends YTNode {
    static type = 'MusicCardShelfHeaderBasic';
    title;
    constructor(data) {
        super();
        this.title = new Text(data.title);
    }
}
//# sourceMappingURL=MusicCardShelfHeaderBasic.js.map