var app=angular.module('dashboard',[])
	.controller('dashboardCtrl',['$scope','$interval','$http',function($scope,$interval,$http){
        $scope.questions={};
        $scope.current=0;
        var update=function(){
            $http.get("/api/results").then(function(response){
                $scope.questions=response.data.data;  
                $scope.questions[$scope.current].show=true;
                $scope.current+=1;
                if($scope.current==$scope.questions.length){
                    $scope.current=0;
                }
        });
        };
        $interval(update,10000);
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

