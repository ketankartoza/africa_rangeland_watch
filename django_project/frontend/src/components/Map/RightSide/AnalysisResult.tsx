import React from 'react';
import { Box, Center, Spinner, Table, Text } from "@chakra-ui/react";
import { useSelector } from "react-redux";
import { RootState } from "../../../store";
import { Analysis } from "../../../store/analysisSlice";
import { Bar, Line } from "react-chartjs-2";
import { CategoryScale } from "chart.js";
import Chart from "chart.js/auto";
import ChartDataLabels from "chartjs-plugin-datalabels";
import {FeatureCollection} from "geojson";
import 'chartjs-adapter-date-fns';

import './style.css';

Chart.register(CategoryScale);

interface Props {
  analysis: Analysis;
}

export function BarChart({ analysis }: Props) {
  // Extracting data for the chart
  const jsonData = analysis.results[0];

  if (jsonData.features.length == 0) {
    return
  }

  let labels: number[] = [jsonData.features[0].properties.year];
  if (jsonData.features.length > 1) {
    labels.push(jsonData.features[jsonData.features.length -1].properties.year);
  }
  const name1 = jsonData.features[0].properties.Name;
  const name2 = jsonData.features.length > 1 ? jsonData.features[1].properties.Name : null;

  const dataBar1 = jsonData.features
    .filter((feature:any) => feature.properties.Name === name1)
    .map((feature:any) => feature.properties[analysis.data.variable]);

  let chartData:any = {
    labels,
    datasets: [
      {
        label: name1,
        data: dataBar1,
        backgroundColor: "blue"
      }
    ],
  };

  if (name2 !== null && name1 != name2) {
    const dataBar2 = jsonData.features
    .filter((feature:any) => feature.properties.Name === name2)
    .map((feature:any) => feature.properties[analysis.data.variable]);

    chartData.datasets.push({
      label: name2,
      data: dataBar2,
      backgroundColor: "red"
    });
  }

  const options:any = {
    responsive: true,
    plugins: {
      legend: {
        position: "top",
      },
      title: {
        display: false,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    }
  };

  return <Box maxWidth={400} overflowX={"auto"}>
    <Bar options={options} data={chartData} />
  </Box>
}

export function LineChart({ analysis }: Props) {
  // Extracting data for the chart

  const jsonData = analysis.results[1];
  if (jsonData.features.length == 0) {
    return
  }

  const name1 = jsonData.features[0].properties.Name;
  const name2 = jsonData.features[1].properties.Name;
  const labels: number[] = jsonData.features
    .filter((feature:any) => feature.properties.Name === name1)
    .map((feature:any) => feature.properties.date);

  const data1 = jsonData.features
    .filter((feature:any) => feature.properties.Name === name1)
    .map((feature:any) => feature.properties[analysis.data.variable]);

  let chartData:any = {
    labels,
    datasets: [
      {
        label: name1,
        data: data1,
        backgroundColor: "blue"
      }
    ],
  };

  if (name1 != name2) {
    const data2 = jsonData.features
    .filter((feature:any) => feature.properties.Name === name2)
    .map((feature:any) => feature.properties[analysis.data.variable]);

    chartData.datasets.push({
      label: name2,
      data: data2,
      backgroundColor: "red"
    });
  }

  const options:any = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: {
        type: 'timeseries',
        title: {
          display: false
        },
        ticks: {
          callback: function (value: any, index: number, ticks: any) {
            const currentLabel = new Date(value).getFullYear();
            const previousLabel = index > 0 ? new Date(ticks[index - 1].value).getFullYear() : null;
            return currentLabel !== previousLabel ? currentLabel : '';
          },
        }
      },
      y: {
        title: {
          display: false
        },
      },
    },
    plugins: {
      legend: {
        position: 'top',
      },
    },
  };

  return <Box maxWidth={400} overflowX={"auto"}>
    <Line options={options} data={chartData}/>
  </Box>
}

function SpatialBarChart({ analysis }: Props) {
  const featureCollection: FeatureCollection = analysis.results;

  const labels: string[] = featureCollection.features.map((feature) => feature.properties['Name'])
  let chartData:any = {
    labels,
    datasets: [
      {
        label: '% difference to reference area',
        data: featureCollection.features.map((feature) => feature.properties["mean"]),
        backgroundColor: "blue"
      }
    ],
  };

  const options:any = {
    responsive: true,
    plugins: {
      legend: {
        position: "top",
      },
      title: {
        display: true,
      },
      subtitle: {
        display: true,
        text: 'Feature (labeled by',
        position: 'bottom'
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'mean'
        }
      },
    }
  };

  return <Box maxWidth={400} overflowX={"auto"}>
    <Bar options={options} data={chartData} />
  </Box>
}


export function RenderBaseline({ analysis }: Props) {
  const keys = Object.keys(analysis.results.columns)
  return <Box maxWidth={400} overflowX={"auto"}>
    <Table className='BaselineAnalysisResultTable' cellPadding={8}>
      <tr>
        <th>Name</th>
        {
          keys.map(
            (column: string) => <th key={column}>{column}</th>
          )
        }
      </tr>
      {
        analysis.results.features.map((feature: any) => {
          const properties = feature.properties;
          return <tr>
            <td>{properties.Name}</td>
            {
              keys.map(
                (column: string) => <td key={column}>
                  {properties[column]}
                </td>
              )
            }
          </tr>
        })
      }
    </Table>
  </Box>
}

export function RenderTemporal({ analysis }: Props) {
  return <Box maxWidth={400} overflowX={"auto"}>
    <BarChart analysis={analysis}></BarChart>
    <LineChart analysis={analysis}></LineChart>
  </Box>
}

export function RenderSpatial({ analysis }: Props) {
  return <Box maxWidth={400} overflowX={"auto"}>
    <Text color='black' marginTop={2}>Relative % difference in {analysis.data.variable} between your reference area and selected camp/s:</Text>
    <SpatialBarChart analysis={analysis} />
  </Box>
}


export function RenderResult({ analysis }: Props) {
  switch (analysis.data.analysisType) {
    case "Baseline":
      return <RenderBaseline analysis={analysis}/>
    case "Temporal":
      return <RenderTemporal analysis={analysis}/>
    case "Spatial":
      return <RenderSpatial analysis={analysis}/>
    default:
      return null
  }
}

/** AnalysisResult component of map. */
export default function AnalysisResult() {
  const {
    loading,
    error,
    analysis
  } = useSelector((state: RootState) => state.analysis);
  if (!loading && !error && !analysis) {
    return null
  }
  return (
    <Box backgroundColor='white'
         borderRadius={8}
         boxShadow="0px 0px 5px 0px #00000030"
         pointerEvents='auto'
         p={4}>
      <Text fontSize="1.5rem" fontWeight={600} color='green.600'>
        Statistics
      </Text>
      {
        loading ?
          <Box>
            <Center p={16}>
              <Spinner size="xl"/>
            </Center>
          </Box> : error ? <Box>
            <Center p={16} color={'red'}>
              {error}
            </Center>
          </Box> : <RenderResult analysis={analysis}/>
      }
    </Box>
  )
}