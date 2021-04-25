import React from 'react';
import {BrowserRouter, Link, Redirect, Route, Switch,} from "react-router-dom";
import './App.css';
import {TrackTable} from './Track'

export const BASE_URL = 'http://localhost:8000'

interface AppProps {
}

interface AppState {
}

class App extends React.Component<AppProps, AppState> {
  constructor(props: AppProps) {
    super(props);
  }

  render() {
    return (
        <BrowserRouter basename="/app">
          <div>
            <nav>
              <ul>
                <li>
                  <Link to="/track">Track</Link>
                </li>
                <li>
                  <Link to="/playlist">Playlist</Link>
                </li>
              </ul>
            </nav>
          </div>

          <Switch>
            <Route path="/track">
              <TrackTable/>
            </Route>
            <Route path="/playlist">
            </Route>
            <Route><Redirect to="/"/></Route>
          </Switch>
        </BrowserRouter>
    )
  }
}


export default App;
