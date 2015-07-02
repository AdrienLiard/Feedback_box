var app=angular.module('dashboard',[])
	.controller('dashboardCtrl',['$scope','$interval','$http',function($scope,$interval,$http){
        $scope.questions={};
       
        var update=function(){
            $http.get("/api/results").then(function(response){
                $scope.questions=response.data.data;  
                
        });
        };
        
        update();
        
        

}]);
app.directive('donut', function() {

    return {

        // required to make it work as an element
        restrict: 'E',
        template: '<div></div>',
        replace: true,
        // observe and manipulate the DOM
        link: function($scope, element, attrs) {
            var data=attrs["values"];
          
            Morris.Donut({
                    element: element,
                    data: angular.fromJson(data)
                    
                });
            
        }

    };

});

