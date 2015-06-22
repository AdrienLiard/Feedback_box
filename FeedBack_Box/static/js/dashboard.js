var app=angular.module('dashboard',[])
	.controller('dashboardCtrl',['$scope','$http',function($scope,$http){
		$scope.questionnaire={};
		$http.get("/api/questionnaire").then(function(response){
			console.log(response);
			$scope.questionnaire=response.data;
		});
		console.log($scope.questionnaire);

	}])
app.directive('barchart', function() {

    return {

        // required to make it work as an element
        restrict: 'E',
        template: '<div></div>',
        replace: true,
        // observe and manipulate the DOM
        link: function($scope, element, attrs) {

            var data = $scope[attrs.data],
                xkey = $scope[attrs.xkey],
                ykeys= $scope[attrs.ykeys],
                labels= $scope[attrs.labels];

            Morris.Bar({
                    element: element,
                    data: data,
                    xkey: xkey,
                    ykeys: ykeys,
                    labels: labels
                });

        }

    };

});
