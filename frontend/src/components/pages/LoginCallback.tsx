import React from 'react';
import {Redirect, RouteComponentProps} from "react-router-dom"
import QueryString from "query-string"
import {BASE_URL} from "./App";


interface Props extends RouteComponentProps {
  setJwt: (jwt: string) => void
}

export class LoginCallback extends React.Component<Props, {}> {
  constructor(props: Props) {
    super(props);
  }

  componentDidMount() {
    const params = QueryString.parse(this.props.location.search)
    if (!params.code) {
      return;
    }
    const url = BASE_URL + "/login/callback?code=" + params.code + "&origin=" + document.location.origin
    fetch(url)
    .then(response => response.json())
    .then(jwt => this.props.setJwt(jwt))
  }

  render() {
    return (
        <Redirect to="/"/>
    )
  }
}

