import { Parser } from '../index.js';
import HeatMarker from './HeatMarker.js';
import { YTNode } from '../helpers.js';
import TimedMarkerDecoration from './TimedMarkerDecoration.js';
export default class Heatmap extends YTNode {
    static type = 'Heatmap';
    max_height_dp;
    min_height_dp;
    show_hide_animation_duration_millis;
    heat_markers;
    heat_markers_decorations;
    constructor(data) {
        super();
        this.max_height_dp = data.maxHeightDp;
        this.min_height_dp = data.minHeightDp;
        this.show_hide_animation_duration_millis = data.showHideAnimationDurationMillis;
        this.heat_markers = Parser.parseArray(data.heatMarkers, HeatMarker);
        this.heat_markers_decorations = Parser.parseArray(data.heatMarkersDecorations, TimedMarkerDecoration);
    }
}
//# sourceMappingURL=Heatmap.js.map