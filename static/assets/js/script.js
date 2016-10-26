type = ['','info','success','warning','danger'];
    	

demo = {
    initPickColor: function(){
        $('.pick-class-label').click(function(){
            var new_class = $(this).attr('new-class');  
            var old_class = $('#display-buttons').attr('data-class');
            var display_div = $('#display-buttons');
            if(display_div.length) {
            var display_buttons = display_div.find('.btn');
            display_buttons.removeClass(old_class);
            display_buttons.addClass(new_class);
            display_div.attr('data-class', new_class);
            }
        });
    },
    
    initChartist: function(){    
        
        var dataSales = {
          labels: ['','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','',],
          series: [
             [287, 385, 490, 492, 554, 586, 698, 695, 752, 788, 846, 944,287, 385, 490, 492, 554, 586, 698, 695, 752, 788, 846, 944,287, 385, 490, 492, 554, 586, 698, 695, 752, 788, 846, 944,287, 385, 490, 492, 554, 586, 698, 695, 752, 788, 846, 944,287, 385, 490, 492, 554, 586, 698, 695, 752, 788, 846, 944,287, 385, 490, 492, 554, 586, 698, 695, 752, 788, 846, 944,287, 385, 490, 492, 554, 586, 698, 695, 752, 788, 846, 944,287, 385, 490, 492, 554, 586, 698, 695, 752, 788, 846, 944,287, 385, 490, 492, 554, 586, 698, 695, 752, 788, 846, 944,]
          ]
        };
        
        var optionsSales = {
          lineSmooth: false,
          low: 0,
          high: 800,
          showArea: true,
          height: "245px",
          axisX: {
            showGrid: false,
          },
          lineSmooth: Chartist.Interpolation.simple({
            divisor: 3
          }),
          showLine: false,
          showPoint: false,
        };
        
        var responsiveSales = [
          ['screen and (max-width: 640px)', {
            axisX: {
              labelInterpolationFnc: function (value) {
                return value[0];
              }
            }
          }]
        ];
    
        Chartist.Line('#chartHours', dataSales, optionsSales, responsiveSales);
    }
}

