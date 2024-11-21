import React, {
  forwardRef,
  useEffect,
  useImperativeHandle,
  useRef,
  useState
} from 'react';
import maplibregl from 'maplibre-gl';
import { Box } from "@chakra-ui/react";
import { useDispatch, useSelector } from "react-redux";
import { AppDispatch, RootState } from "../../store";
import { BasemapControl, LegendControl } from "./control";
import { hasSource, removeLayer } from "./utils";
import { fetchBaseMaps } from '../../store/baseMapSlice';
import { fetchMapConfig } from '../../store/mapConfigSlice';
import { Layer } from '../../store/layerSlice';

import 'maplibre-gl/dist/maplibre-gl.css';
import './style.css';

interface Props {

}

/**
 * MapLibre component.
 */
export const MapLibre = forwardRef(
  (props: Props, ref
  ) => {
    const dispatch = useDispatch<AppDispatch>();
    const legendRef = useRef(null);
    const baseMapRef = useRef(null);
    const [map, setMap] = useState(null);
    const { mapConfig } = useSelector((state: RootState) => state.mapConfig);
    const { baseMaps } = useSelector((state: RootState) => state.baseMap);
    const { selected: selectedLandscape } = useSelector((state: RootState) => state.landscape);

    //  Fetch the data here
    useEffect(() => {
      dispatch(fetchBaseMaps())
      dispatch(fetchMapConfig())
    }, [dispatch]);

    // Toggle
    useImperativeHandle(ref, () => ({
      /** Render layer */
      renderLayer(layer: Layer) {
        if (map) {
          const ID = `layer-${layer.id}`
          removeLayer(map, ID)
          if (layer.type == "raster") {
            if (!hasSource(map, ID)) {
              map.addSource(ID, {
                  type: "raster",
                  tiles: [layer.url],
                  tileSize: 256
                }
              )
            }
            map.addLayer(
              {
                id: ID,
                source: ID,
                type: "raster"
              }
            )
            legendRef?.current?.renderLayer(layer)
          }
        }
      },
      /** Hide layer */
      removeLayer(layer: Layer) {
        if (map) {
          const ID = `layer-${layer.id}`
          removeLayer(map, ID)
          legendRef?.current?.removeLayer(layer)
        }
      }
    }));

    /** First initiate */
    useEffect(() => {
      if (baseMaps.length == 0 || !mapConfig) {
        return;
      }
      if (!map) {
        const _map = new maplibregl.Map({
          container: 'map',
          style: {
            version: 8,
            sources: {},
            layers: [],
            glyphs: "/static/fonts/{fontstack}/{range}.pbf"
          },
          center: [0, 0],
          zoom: 1
        });
        _map.once("load", () => {
          setMap(_map)

          _map.fitBounds(mapConfig.initial_bound,
            {
              pitch: 0,
              bearing: 0
            }
          )

          // render default base map
          baseMapRef?.current?.setBaseMapLayer(baseMaps[0])
        })
        _map.addControl(new BasemapControl(baseMaps, baseMapRef), 'bottom-left');
        _map.addControl(new LegendControl(legendRef), 'top-left');
        _map.addControl(new maplibregl.NavigationControl(), 'bottom-left');
      }
    }, [baseMaps, mapConfig]);

    // zoom when landscape is selected
    useEffect(() => {
      if (!map || !selectedLandscape) {
        return;
      }
      map.fitBounds(selectedLandscape.bbox,
        {
          pitch: 0,
          bearing: 0
        }
      )
    }, [selectedLandscape])

    return (
      <Box id="map" flexGrow={1}/>
    )
  }
)

