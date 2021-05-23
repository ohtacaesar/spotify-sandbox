import React from 'react';
import {BrowserRouter, Link, Redirect, Route, Switch,} from "react-router-dom";
import './index.css';
import {RankingPage} from "../RankingPage";
import {JwtContext} from "../../../contexts/JwtContext";
import {Login} from "../Login";
import {LoginCallback} from "../LoginCallback";

export const BASE_URL = 'http://localhost:8000'


interface AppState {
  jwt: string;
}

class App extends React.Component<{}, AppState> {
  constructor(props: {}) {
    super(props);
    this.state = {
      jwt: localStorage.getItem("jwt") || ""
    }
  }

  setJwt(jwt: string) {
    localStorage.setItem("jwt", jwt);
    this.setState({
      jwt: jwt
    })
  }

  render() {
    return <JwtContext.Provider value={this.state.jwt}>
      <BrowserRouter basename="/app">
        <div>
          <nav>
            <ul>
              <li>
                <Link to="/ranking">Ranking</Link>
              </li>
              <li>
                <Link to="/playlist">Playlist</Link>
              </li>
              <li>
                <Link to="/login">Login</Link>
              </li>
            </ul>
          </nav>
        </div>
        <Switch>
          <Route path="/ranking" component={RankingPage}/>
          <Route path="/playlist"/>
          <Route exact path="/login" component={Login}/>
          <Route exact path="/login/callback"
                 render={(props) => (
                     <LoginCallback {...props} setJwt={this.setJwt.bind(this)}/>)}/>
          <Route><Redirect to="/"/></Route>
        </Switch>
      </BrowserRouter>
    </JwtContext.Provider>
  }
}


export default App;
