import React from 'react';
import {BASE_URL} from "./App";

export class Login extends React.Component<any, any> {

  login() {
    const url = BASE_URL + "/login?origin=" + document.location.origin;
    window.location.href = url;
  }

  render() {
    return (
        <div>
          <button onClick={() => this.login()}>ログイン</button>
        </div>
    )
  }
}

