import { YTNode } from '../helpers.js';
export default class PlayerLiveStoryboardSpec extends YTNode {
    static type = 'PlayerLiveStoryboardSpec';
    board;
    constructor(data) {
        super();
        const [template_url, thumbnail_width, thumbnail_height, columns, rows] = data.spec.split('#');
        this.board = {
            type: 'live',
            template_url,
            thumbnail_width: parseInt(thumbnail_width, 10),
            thumbnail_height: parseInt(thumbnail_height, 10),
            columns: parseInt(columns, 10),
            rows: parseInt(rows, 10)
        };
    }
}
//# sourceMappingURL=PlayerLiveStoryboardSpec.js.map