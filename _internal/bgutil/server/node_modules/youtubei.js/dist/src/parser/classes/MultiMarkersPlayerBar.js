import { YTNode, observe } from '../helpers.js';
import { Parser } from '../index.js';
import Chapter from './Chapter.js';
import Heatmap from './Heatmap.js';
export class Marker extends YTNode {
    static type = 'Marker';
    marker_key;
    value;
    constructor(data) {
        super();
        this.marker_key = data.key;
        this.value = {};
        if (Reflect.has(data, 'value')) {
            if (Reflect.has(data.value, 'heatmap')) {
                this.value.heatmap = Parser.parseItem(data.value.heatmap, Heatmap);
            }
            if (Reflect.has(data.value, 'chapters')) {
                this.value.chapters = Parser.parseArray(data.value.chapters, Chapter);
            }
        }
    }
}
export default class MultiMarkersPlayerBar extends YTNode {
    static type = 'MultiMarkersPlayerBar';
    markers_map;
    constructor(data) {
        super();
        this.markers_map = observe(data.markersMap?.map((marker) => new Marker(marker)) || []);
    }
}
//# sourceMappingURL=MultiMarkersPlayerBar.js.map