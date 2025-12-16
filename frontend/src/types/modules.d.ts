declare module 'react-plotly.js' {
  import { Component } from 'react'
  
  interface PlotParams {
    data: any[]
    layout?: any
    config?: any
    style?: React.CSSProperties
    className?: string
    useResizeHandler?: boolean
    onInitialized?: (figure: any, graphDiv: HTMLElement) => void
    onUpdate?: (figure: any, graphDiv: HTMLElement) => void
    onPurge?: (figure: any, graphDiv: HTMLElement) => void
    onError?: (err: Error) => void
  }
  
  export default class Plot extends Component<PlotParams> {}
}

declare module 'leaflet/dist/leaflet.css'
