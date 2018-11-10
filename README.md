# Rockstat Calltracking service example

## Guide

### Clone service

Open Theia IDE terminal

```
cd my_images
git clone 
```

### Define phone pool

Configuration at `config.yml`

```yaml
# Listen all events
rpc_params:
  listen_all: yes

# Project for limitation
project_id: 1382996643

# Phones pool
phones:
  dyn_phones:
    - 74994031705
    - 74994040139
    - 74994040921
    - 74994033095
    - 74994040239
    - 74994041156
  fallback: null
```

### Front-end

Put this code after `rstat('configure'...)`.

```js
rstat('onReady', function(){
    var formatPhone = function(num){
      return num.replace(/(\d{1})(\d{3})(\d{3})(\d{2})(\d{2})/, '+$1($2) $3-$4-$5')
    }
    var requestPhone = function(){
      rstat('request', 'ctrack', 'phone_request').then(function(msg){
        if (msg.data && msg.data.num){
          var phone = String(msg.data.num);
          // Your phone block selector
          $('.phone-num').text(formatPhone(phone));
        }
      });
    }
    requestPhone();
    rstat('onEvent', function(name, data){
      if (name === 'session'){
        setTimeout(function(){
          requestPhone();
        }, 100)
      }
    })
});
```

## License

```
Copyright 2018 Dmitry Rodin

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```